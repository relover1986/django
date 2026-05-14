import json, smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import date
from django.core.management.base import BaseCommand
from app01 import models


class Command(BaseCommand):
    help = '发送当日岩工报药汇总邮件'

    def handle(self, *args, **options):
        with open('/root/.email_config.json') as f:
            cfg = json.load(f)

        today = date.today().strftime('%Y年%-m月%-d日')
        records = models.BlastingSummary.objects.filter(date=today).order_by('-created_at')
        count = records.count()

        if count == 0:
            self.stdout.write('NO_DATA')
            return

        rows = ''
        for i, r in enumerate(records, 1):
            shift = r.shift or '-'
            blaster = r.blaster or '-'
            rows += '<tr style=text-align:center;><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%s</td></tr>' % (
                i, shift, r.person, r.location, r.detonator_count, r.explosive_count, blaster)

        html = '<html><body>'
        html += '<h2 style=color:#165DFF;>%s 岩工报药汇总</h2>' % today
        html += '<p>共 <strong>%d</strong> 条记录</p>' % count
        html += '<table border=1 cellpadding=8 cellspacing=0 style=border-collapse:collapse;width:100;max-width:700;>'
        html += '<thead><tr style=background:#0d6efd;color:#fff;text-align:center;><th>#</th><th>班次</th><th>人员</th><th>地点</th><th>雷管数</th><th>炸药(kg)</th><th>爆破员</th></tr></thead>'
        html += '<tbody>' + rows + '</tbody></table>'
        html += '<p style=color:#999;font-size:12px;>由 Hermes Agent 自动发送</p></body></html>'

        msg = MIMEText(html, 'html', 'utf-8')
        msg['From'] = 'Hermes <%s>' % cfg['user']
        msg['To'] = cfg['user']
        msg['Subject'] = str(Header('%s 岩工报药汇总' % today, 'utf-8'))

        server = smtplib.SMTP(cfg['host'], cfg['port'])
        server.starttls()
        server.login(cfg['user'], cfg['auth_code'])
        server.sendmail(cfg['user'], [cfg['user']], msg.as_string())
        server.quit()

        self.stdout.write('EMAIL_SENT %d records' % count)
