from base.action import BaseExchangeAction
from exchangelib import EWSDateTime


class GetCalendarItems(BaseExchangeAction):
    def run(self, start_year, start_day, start_month, end_year, end_day, end_month):
        items = self.account.calendar.filter(
            start__lt=self.timezone.localize(EWSDateTime(end_year, end_month, end_day)),
            end__gt=self.timezone.localize(EWSDateTime(start_year, start_month, start_day)),
        )
        results = []
        self.logger.info('Found {0} calendar entries'.format(len(items)))
        for item in items:
            results.append({
                'start': item.start,
                'end': item.end,
                'subject': item.subject,
                'body': item.body,
                'location': item.location})
        return results
