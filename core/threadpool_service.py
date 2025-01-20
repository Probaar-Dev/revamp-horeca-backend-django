from concurrent.futures import ThreadPoolExecutor


class ThreadPoolService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ThreadPoolService, cls).__new__(cls)
            # The actual initialization is moved from __init__ to here
            cls._instance.notificationsExecutor = ThreadPoolExecutor(max_workers=2)
        return cls._instance

    def get_notification_executor(self) -> ThreadPoolExecutor:
        return self.notificationsExecutor

    def clean(self):
        self.notificationsExecutor.shutdown(wait=True)
