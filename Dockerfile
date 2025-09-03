FROM python:3.9-alpine


# RUN apt-get update && apt-get install -y \
#     gcc \
#     default-libmysqlclient-dev \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание скрипта для ожидания базы данных
# RUN echo '#!/bin/bash\n\
# while ! nc -z mysql 3306; do\n\
#   echo "Waiting for MySQL..."\n\
#   sleep 1\n\
# done\n\
# echo "MySQL is up!"' > /wait_for_db.sh && chmod +x /wait_for_db.sh

# RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# # Создание псевдонима для wait_for_db
# RUN echo '#!/bin/bash\n\
# /wait_for_db.sh\n\
# exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# ENTRYPOINT ["/entrypoint.sh"]