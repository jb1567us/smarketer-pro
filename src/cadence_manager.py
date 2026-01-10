import json
import time
from database import (
    create_sequence, add_sequence_step, enroll_lead_in_sequence, 
    get_due_enrollments, get_sequence_steps, update_enrollment_progress,
    mark_contacted, get_connection
)
from agents import CopywriterAgent
from mailer import Mailer

class CadenceManager:
    def __init__(self):
        self.copywriter = CopywriterAgent()
        self.mailer = Mailer()

    def build_campaign_sequence(self, campaign_id, campaign_name, context_str, steps=3):
        """
        Generates a sequence for a campaign and saves it to DB.
        """
        # 1. Generate via AI
        sequence_data = self.copywriter.generate_sequence(context_str, steps=steps)
        
        # 2. Create Sequence record
        seq_id = create_sequence(campaign_id, f"Cadence for {campaign_name}")
        
        # 3. Save steps
        for step in sequence_data:
            add_sequence_step(
                sequence_id=seq_id,
                step_number=step['step_number'],
                touch_type=step['touch_type'],
                delay_days=step['delay_days'],
                content_json=json.dumps({
                    "subject": step['subject'],
                    "body": step['body']
                })
            )
        return seq_id

    def process_all_cadences(self):
        """
        The 'Heartbeat': Finds all due enrollments and executes the next step.
        """
        due_list = get_due_enrollments()
        results = []
        
        for enrollment in due_list:
            # Get steps for this sequence
            steps = get_sequence_steps(enrollment['sequence_id'])
            current_idx = enrollment['current_step_index']
            
            if current_idx < len(steps):
                step = steps[current_idx]
                
                # Execute touch
                success = self._execute_step(enrollment, step)
                
                if success:
                    # Calculate next scheduled time
                    next_idx = current_idx + 1
                    status = 'active'
                    next_scheduled = 0
                    
                    if next_idx < len(steps):
                        # Schedule next step based on its delay_days
                        next_step = steps[next_idx]
                        next_scheduled = int(time.time()) + (next_step['delay_days'] * 86400)
                    else:
                        status = 'completed'
                        next_scheduled = 0
                    
                    update_enrollment_progress(
                        enrollment_id=enrollment['id'],
                        next_step_index=next_idx,
                        next_scheduled_at=next_scheduled,
                        status=status
                    )
                    results.append({"enrollment_id": enrollment['id'], "status": "sent"})
                else:
                    results.append({"enrollment_id": enrollment['id'], "status": "failed"})
            else:
                # Already finished but status wasn't updated?
                update_enrollment_progress(enrollment['id'], current_idx, 0, 'completed')
                
        return results

    def _execute_step(self, enrollment, step):
        """
        Internal dispatcher for different touch types.
        """
        content = json.loads(step['content_json'])
        email_addr = enrollment['email']
        
        # Personalize
        subject = content['subject']
        body = content['body']
        
        contact = enrollment.get('contact_person') or "there"
        biz = enrollment.get('company_name') or "your business"
        
        subject = subject.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
        body = body.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
        
        if step['touch_type'] == 'email':
            try:
                if self.mailer.send_email(email_addr, subject, body):
                    mark_contacted(email_addr)
                    return True
            except Exception as e:
                print(f"Cadence Send Error: {e}")
                return False
        
        # Placeholder for other touch types (LinkedIn, etc.)
        return False
