import reflex as rx
from .base import BaseState, DB_AVAILABLE
from ..models import Lead

class LeadState(BaseState):
    """Lead management state."""
    # Leads Data
    leads: list[Lead] = []
    selected_lead_ids: list[int] = []
    lead_search_query: str = ""
    lead_status_filter: str = "All"
    leads_loaded: bool = False
    
    # Pagination State
    leads_page: int = 1
    leads_page_size: int = 15
    leads_total: int = 0
    
    @rx.var
    def total_leads(self) -> int:
        return self.leads_total
    
    # Detail View State
    selected_lead: Lead | None = None
    is_detail_open: bool = False
    
    # Pipeline State
    pipeline_stats: dict = {}

    @rx.var
    def pipeline_columns(self) -> list[dict]:
        """Computed var for Kanban columns."""
        stats = self.pipeline_stats
        return [
            {"name": "Discovery", "status": "new", "count": stats.get("new", {}).get("count", 0), "value": stats.get("new", {}).get("value", 0), "color": "indigo"},
            {"name": "Qualified", "status": "qualified", "count": stats.get("qualified", {}).get("count", 0), "value": stats.get("qualified", {}).get("value", 0), "color": "blue"},
            {"name": "Negotiation", "status": "negotiation", "count": stats.get("negotiation", {}).get("count", 0), "value": stats.get("negotiation", {}).get("value", 0), "color": "orange"},
            {"name": "Closed Won", "status": "closed", "count": stats.get("closed", {}).get("count", 0), "value": stats.get("closed", {}).get("value", 0), "color": "green"},
        ]

    async def load_leads(self):
        """Load leads from database with pagination and filtering."""
        if DB_AVAILABLE:
            try:
                from backend.database import get_leads_paginated, get_total_leads_count, get_pipeline_stats
                # Fetch more for client-side filtering (prototype only)
                raw_leads = get_leads_paginated(page=self.leads_page, page_size=100)
                
                filtered = []
                for l in raw_leads:
                    email = (l.get("email") or "").lower()
                    company = (l.get("company_name") or "").lower()
                    status = (l.get("status") or "").lower()
                    search = self.lead_search_query.lower()
                    
                    if self.lead_status_filter != "All" and status != self.lead_status_filter.lower():
                        continue
                    if search and (search not in email and search not in company):
                        continue
                        
                    filtered.append(l)
                
                async with self:
                    self.leads = [Lead(**l) for l in filtered]
                    self.leads_total = get_total_leads_count()
                    self.pipeline_stats = get_pipeline_stats()
            except Exception as e:
                print(f"Error loading leads: {e}")
                self.leads = []
                self.leads_total = 0
        else:
             self.leads = []
             self.leads_total = 0
             
        async with self:
            self.leads_loaded = True
        
    async def set_lead_search_query(self, query: str):
        self.lead_search_query = query
        await self.load_leads()
        
    async def set_lead_status_filter(self, status: str):
        self.lead_status_filter = status
        await self.load_leads()

    async def delete_lead(self, lead_id: int):
        """Delete a lead."""
        if DB_AVAILABLE:
            from backend.database import delete_leads
            delete_leads([lead_id])
            self.add_log(f"Deleted lead ID {lead_id}")
            await self.load_leads()

    def next_page(self):
        """Go to next page of leads."""
        if self.leads_page * self.leads_page_size < self.leads_total:
            self.leads_page += 1
            return LeadState.load_leads

    def prev_page(self):
        """Go to previous page of leads."""
        if self.leads_page > 1:
            self.leads_page -= 1
            return LeadState.load_leads
            
    def select_lead(self, lead: Lead):
        """Open detail modal for a lead."""
        self.selected_lead = lead
        self.is_detail_open = True
        
    def close_detail(self):
        """Close detail modal."""
        self.is_detail_open = False
        self.selected_lead = None

    async def delete_selected_leads(self):
        """Delete selected leads."""
        if DB_AVAILABLE and self.selected_lead_ids:
            try:
                from backend.database import delete_leads
                delete_leads(self.selected_lead_ids)
                self.selected_lead_ids = []
                await self.load_leads()
            except Exception as e:
                print(f"Error deleting leads: {e}")

    async def handle_import(self, files: list[rx.UploadFile]):
        """Handle uploaded files for lead import."""
        from backend.logic.importer import DataImporter
        import os
        import tempfile
        
        importer = DataImporter()
        total_results = {"imported": 0, "duplicates": 0, "errors": 0}
        
        for file in files:
            # Save file to temp location
            out_path = os.path.join(tempfile.gettempdir(), file.filename)
            with open(out_path, "wb") as f:
                f.write(await file.read())
            
            # Run import
            if file.filename.endswith(".csv"):
                res = await importer.import_from_csv(out_path)
            elif file.filename.endswith(".json"):
                res = await importer.import_from_json(out_path)
            else:
                self.add_log(f"Unsupported file type: {file.filename}")
                continue
                
            if res.get("status") == "success":
                total_results["imported"] += res.get("imported", 0)
                total_results["duplicates"] += res.get("duplicates", 0)
                total_results["errors"] += res.get("errors", 0)
            
            # Cleanup
            try: os.remove(out_path)
            except: pass

        self.add_log(f"Import Complete: {total_results['imported']} new, {total_results['duplicates']} dups, {total_results['errors']} errors")
        await self.load_leads()
        return rx.window_alert(f"Import results: {total_results['imported']} new leads added.")

    async def export_leads_csv(self):

        """Export leads to CSV."""
        import pandas as pd
        import io
        if not self.leads:
            return rx.window_alert("No leads to export")
        
        try:
            # Convert Lead objects to dicts
            data = [l.dict() for l in self.leads]
            df = pd.DataFrame(data)
            csv_data = df.to_csv(index=False)
            self.add_log(f"Exported {len(data)} leads to CSV")
            return rx.download(data=csv_data, filename="leads_export.csv")
        except Exception as e:
            self.add_log(f"Export failed: {e}")
            return rx.window_alert(f"Export error: {e}")

    async def export_leads_excel(self):
        """Export leads to Excel."""
        import pandas as pd
        import io
        if not self.leads:
            return rx.window_alert("No leads to export")
        
        try:
            data = [l.dict() for l in self.leads]
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            self.add_log(f"Exported {len(data)} leads to Excel")
            return rx.download(data=output.getvalue(), filename="leads_export.xlsx")
        except Exception as e:
            self.add_log(f"Export failed: {e}")
            return rx.window_alert(f"Export error: {e}")

