from celery_worker import celery_app


class TaskRegistry:
    """Registry for managing Celery tasks."""
    
    @staticmethod
    def register_tasks():
        """
        Import task modules to register them with Celery.
        Tasks should use @celery_app.task decorator in their own files.
        """
        # Import task modules - this will trigger @celery_app.task decorators
        from task import cv_parsing_task
        from task import send_email_invitation_task
        
        print("✅ Task modules imported and registered!")


# Auto-register all tasks when this module is imported
TaskRegistry.register_tasks()
