from square.client import Client as squareClient
from datetime import datetime, timezone

apiKey = ''

class ApiRequestError(Exception):
    def __init__(self, message):
        super().__init__(message)

def CheckRequest(apiResponse):
    if 'errors' in apiResponse.body: 
        e = apiResponse.body['errors'][0]
        raise ApiRequestError('%s: %s: %s'%(e['category'], e['code'], e['detail']))
    else: return apiResponse

class Employee:
    def __init__(self, employee_id, location):
        self.location = location
        self.employeeID = employee_id
        self.client = squareClient(access_token=apiKey, environment='production')

    def punch(self):
        _client = self.client.labor
        timecards = _client.search_shifts(body = {
                "query": {
                    "filter": {
                        "employee_ids": [
                            self.employeeID
                        ]
                    }
                }
            })
        
        # Searches for first Open Timecard
        if CheckRequest(timecards).body != {}:
            for _shift in timecards.body['shifts']:
                if _shift['status'] == 'OPEN': return self._punch_out(_shift['id'], _shift['start_at'])
        
        # Punch In
        _time = datetime.now(timezone.utc).isoformat()
        _timecard = _client.create_shift(body={
            'shift': {
                'employee_id':self.employeeID,
                'start_at': _time,
                'location_id':self.location
            }
        })
        
        return CheckRequest(_timecard).body['shift']['start_at'], True

    # Private Function: Only to be used if there is an open shift
    def _punch_out(self, shiftID, startTime):
        _client = self.client.labor
        _wage = CheckRequest(_client.list_employee_wages(employee_id=self.employeeID)).body['employee_wages'][0]
        _time = datetime.now(timezone.utc).isoformat()
        _timecard = _client.update_shift(id=shiftID, body={
            'shift': {
                'employee_id':self.employeeID,
                'location_id':self.location,
                'start_at':startTime,
                'end_at':_time,
                'wage': {
                    'title': _wage['title'],
                    'hourly_rate': _wage['hourly_rate']
                    }
            }
        })
        
        return CheckRequest(_timecard).body['shift']['end_at'], False
