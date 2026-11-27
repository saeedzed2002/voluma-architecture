FROM nginx:1.30.7-alpine-slim@sha256:8c950211a641ec5b23f265450517001f6bcca533666120ebe36cb4cff3d00a55

COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/conf.d/media.conf /etc/nginx/conf.d/media.conf
COPY infra/nginx/conf.d/proxy-headers.conf /etc/nginx/conf.d/proxy-headers.conf
COPY --chmod=755 infra/nginx/entrypoint.sh /usr/local/bin/voluma-nginx-entrypoint

EXPOSE 8080 8443

ENTRYPOINT ["/usr/local/bin/voluma-nginx-entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
