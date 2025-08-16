FROM python:3.13.6
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV DISCORD_BOT_TOKEN=MTM1NDAzNDY3MjAzMTc2MDQyNg.GEpqxN.2CvPMHT7wlhLJHGXF8iYP5eHckPu9GBqTScMtI

RUN useradd eroarchives
USER eroarchives

CMD ["python", "src/main.py"]