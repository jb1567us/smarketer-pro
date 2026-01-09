from abc import ABC, abstractmethod

class VideoProvider(ABC):
    """
    Abstract base class for all video generation providers.
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key

    @abstractmethod
    def generate_video(self, prompt, **kwargs):
        """
        Starts a video generation job.
        Should return a dictionary with at least 'job_id' and 'status'.
        
        :param prompt: Text description of the video
        :param kwargs: Additional parameters like aspect_ratio, duration, etc.
        """
        pass

    @abstractmethod
    def get_status(self, job_id):
        """
        Checks the status of a generation job.
        Should return a dictionary with 'status', 'url' (if complete), 'progress' (optional).
        """
        pass
