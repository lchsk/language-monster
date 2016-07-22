import uuid

from rest_framework.decorators import api_view
from core.models import *

from api.helper.api_call import *
from utility.api_utils import validate
from django.core.urlresolvers import reverse


@api_view(['POST'])
@validate('devices')
def devices(request, *args, **kwargs):
    """
        API call to register new device
    """

    if request.method == METHOD_POST:
        try:
            d = request.data

            device_key = uuid.uuid4().hex

            device = MobileDevice(
                os=d.get('os', ''),
                device_key=device_key,
                ip=d.get('ip', ''),
                device=d.get('device', ''),
                display=d.get('display', ''),
                hardware=d.get('hardware', ''),
                manufacturer=d.get('manufacturer', ''),
                model=d.get('model', ''),
                sdk=d.get('sdk', ''),
                language=d.get('language', '')
            )

            device.save()

            resp = {
                'device_key': device_key
            }

            return success(resp)

        except Exception, e:
            return error(RESP_SERV_ERR, str(e))

    return error(RESP_METHOD_NOT_ALLOWED)
