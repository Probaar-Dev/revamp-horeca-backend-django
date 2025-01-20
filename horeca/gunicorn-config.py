from core.threadpool_service import ThreadPoolService


def worker_exit(server, worker):
    ThreadPoolService().clean()

