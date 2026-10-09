FROM node:24-alpine AS game
WORKDIR /build
COPY apps/game/package*.json ./
RUN npm ci
COPY apps/game ./
ARG VITE_DISCORD_CLIENT_ID
ENV VITE_DISCORD_CLIENT_ID=$VITE_DISCORD_CLIENT_ID
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements.txt /app/apps/api/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/api/requirements.txt
COPY apps/api /app/apps/api
COPY apps/bot/tourwork /app/apps/bot/tourwork
ENV TZ=Europe/Paris
VOLUME /app/data
COPY --from=game /build/dist /app/apps/game/dist
ENV PORT=10080
EXPOSE 10080
CMD ["python","apps/api/server.py"]
