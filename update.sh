git pull
python -m pip install -r requirements.txt
python manage.py makemigrations parameter xauth
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py populate
sudo chown -R $USER:www-data .
sudo chmod -R a-rwx,u+rwx,g+rwx mediafiles
sudo systemctl reload apache2.service
