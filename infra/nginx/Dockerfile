FROM nginx:1.30.4-alpine@sha256:dc5069ad14f19660b141b21236140b91656bf89bbc3e2417c70ae650cd66104c

COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/conf.d/media.conf /etc/nginx/conf.d/media.conf
COPY infra/nginx/conf.d/proxy-headers.conf /etc/nginx/conf.d/proxy-headers.conf

RUN mkdir --parents /tmp/nginx/client /tmp/nginx/proxy /tmp/nginx/fastcgi /tmp/nginx/uwsgi /tmp/nginx/scgi \
    && chown -R nginx:nginx /tmp/nginx

USER nginx

EXPOSE 8080 8443
