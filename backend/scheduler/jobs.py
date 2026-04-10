from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown()
