from hc.api.models import Check, Ping
from hc.test import BaseTestCase


class StatusSingleTestCase(BaseTestCase):

    def setUp(self):
        super(StatusSingleTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_it_works(self):
        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/%s/status/" % self.check.code)
        doc = r.json()

        self.assertEqual(doc["status"], "new")
        self.assertTrue("never received a ping" in doc["status_text"])
        self.assertTrue("not received any pings yet" in doc["events"])

    def test_it_returns_events(self):
        p = Ping.objects.create(owner=self.check, ua="test-user-agent", n=1)
        self.check.status = "up"
        self.check.last_ping = p.created
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/checks/%s/status/" % self.check.code)
        doc = r.json()

        self.assertEqual(doc["status"], "up")
        self.assertEqual(doc["updated"], p.created.strftime("%s.%f"))
        self.assertTrue("test-user-agent" in doc["events"])

    def test_it_omits_events(self):
        p = Ping.objects.create(owner=self.check, ua="test-user-agent", n=1)
        self.check.status = "up"
        self.check.last_ping = p.created
        self.check.save()

        timestamp = p.created.strftime("%s.%f")
        url = "/checks/%s/status/?u=%s" % (self.check.code, timestamp)

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get(url)
        doc = r.json()

        self.assertFalse("events" in doc)
