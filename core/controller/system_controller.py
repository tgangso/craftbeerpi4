from aiohttp import web
from aiojobs.aiohttp import get_scheduler_from_app

from core.api.decorator import request_mapping


class SystemController():
    name = "Manuel"

    def __init__(self, core):
        self.core = core
        self.service = core.actor
        self.core.register(self, "/system")

    @request_mapping("/jobs", method="GET", name="get_jobs", auth_required=True)
    def get_all_jobs(self, request):
        scheduler = get_scheduler_from_app(self.core.app)
        print(scheduler.active_count, scheduler.pending_limit)
        for j in scheduler:
            print(j)

            # await j.close()
        return web.Response(text="HALLO")