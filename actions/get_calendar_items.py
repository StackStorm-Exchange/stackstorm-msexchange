from base.action import BaseExchangeAction
from exchangelib import EWSDateTime


class GetCalendarItems(BaseExchangeAction):
    def run(self, start_year, start_day, start_month, end_year, end_day, end_month):
        items = self.account.calendar.filter(
            start__lt=self.timezone.localize(EWSDateTime(end_year, end_month, end_day)),
            end__gt=self.timezone.localize(EWSDateTime(start_year, start_month, start_day)),
        )

        self.logger.info('Found {0} calendar entries'.format(len(items)))
        return [self._format_item(item) for item in items]

    def _format_item(self, item):
        return {
            'start': item.start,
            'end': item.end,
            'subject': item.subject,
            'body': item.body,
            'location': item.location
        }
