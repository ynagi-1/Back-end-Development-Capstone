#!/bin/sh

set -e
python manage.py migrate --noinput
python manage.py shell -c "from concert.models import Concert; Concert.objects.get_or_create(concert_name='Djirection Live', defaults={'duration':3,'city':'Astana','date':'2027-04-14'})"

exec "$@"
