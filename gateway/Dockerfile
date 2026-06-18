# Deployment Artifact - pinned nginxinc/nginx-unprivileged image, non-root runtime.
# SAD Traceability: local API Gateway representing Cliente -> API Gateway -> FleetOps Reports.
FROM nginxinc/nginx-unprivileged:1.27.5-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

