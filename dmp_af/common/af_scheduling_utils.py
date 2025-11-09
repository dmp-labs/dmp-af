from datetime import datetime
from functools import partial
from typing import Callable

from croniter import croniter, croniter_range

from dmp_af.common.scheduling import BaseScheduleTag
from dmp_af.parser.dbt_node_model import WaitPolicy


class _TaskScheduleMapping:
    def __init__(self, wait_policy: WaitPolicy):
        self.wait_policy = wait_policy

        self._mapping: dict[tuple[str, str], list[Callable[..., datetime | None] | None]] = {}

    def is_registered(self, upstream_schedule_tag: BaseScheduleTag, downstream_schedule_tag: BaseScheduleTag) -> bool:
        return (upstream_schedule_tag.name, downstream_schedule_tag.name) in self._mapping

    def add(
        self,
        upstream_schedule_tag: BaseScheduleTag,
        downstream_schedule_tag: BaseScheduleTag,
        fn: Callable[..., datetime | None] | list[Callable[..., datetime | None]],
    ):
        fn_list: list[Callable[..., datetime | None] | None]
        if not isinstance(fn, list):
            fn_list = [fn]
        else:
            fn_list = list(fn)  # Cast to allow None in list
        self._mapping[(upstream_schedule_tag.name, downstream_schedule_tag.name)] = fn_list
        return self

    @staticmethod
    def _update_upstream_cron_args(
        fn: Callable[..., datetime | None] | None, upstream: BaseScheduleTag, downstream: BaseScheduleTag
    ):
        if fn is None or not isinstance(fn, partial):
            return

        fn.keywords.update({'self_schedule': downstream, 'upstream_schedule': upstream})

    def get(
        self, key: tuple[BaseScheduleTag, BaseScheduleTag], default=None
    ) -> list[Callable[..., datetime | None] | None]:
        """
        If the result function is None (or list of None),
        it means that there is no need to find a specific upstream task, wait for the last one.
        """
        if not isinstance(default, list):
            default = [default]
        stream_names = (key[0].name, key[1].name)
        fns: list[Callable[..., datetime | None] | None] = self._mapping.get(stream_names, default)
        for fn in fns:
            self._update_upstream_cron_args(fn, upstream=key[0], downstream=key[1])

        return fns


def calculate_task_to_wait_execution_date(
    execution_date: datetime,
    self_schedule: BaseScheduleTag,
    upstream_schedule: BaseScheduleTag,
    num_iter: int | None = None,
) -> datetime | None:
    """
    this function calculates the correct nearest execution date for the upstream task to wait for.

    :param num_iter: number of iterations to go back in time
        by default it's None, which means that the function will return the last possible execution date.
        this parameter is used for the 'all' wait policy to iterate over all possible execution dates
    """
    self_cron = self_schedule.cron_expression()
    upstream_cron = upstream_schedule.cron_expression()
    assert self_cron is not None, 'Manual schedules cannot be used in dependency calculations'
    assert upstream_cron is not None, 'Manual schedules cannot be used in dependency calculations'

    interval_stop_dttm: datetime = croniter(self_cron.raw_cron_expression, execution_date).get_next(datetime)

    if self_schedule < upstream_schedule:
        cron_iter = croniter(upstream_cron.raw_cron_expression, interval_stop_dttm)
        cron_iter.get_prev()
        return cron_iter.get_prev(datetime)
    if self_schedule == upstream_schedule:
        if self_schedule.timeshift == upstream_schedule.timeshift:
            return execution_date
        cron_iter = croniter(upstream_cron.raw_cron_expression, execution_date)
        return cron_iter.get_prev(datetime)

    all_dts = list(
        croniter_range(execution_date, interval_stop_dttm, upstream_cron.raw_cron_expression, ret_type=datetime)
    )

    if all_dts and all_dts[-1] == interval_stop_dttm:
        all_dts.pop()

    if num_iter is None:
        return all_dts[-1]

    return all_dts[num_iter]


GLOBAL_TASK_SCHEDULE_MAPPINGS = {policy: _TaskScheduleMapping(policy) for policy in WaitPolicy}
