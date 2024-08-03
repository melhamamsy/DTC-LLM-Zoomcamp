<!-- pgcli postgresql://postgres:example@localhost:5432/course_assistant -->

./setup.sh
python generate_data.py
python create_grafana_dashboards.py