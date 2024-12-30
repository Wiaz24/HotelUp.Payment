# HotelUp - Payment service
![dockerhub_badge](https://github.com/Wiaz24/HotelUp.Payment/actions/workflows/dockerhub.yml/badge.svg)

This service should expose endpoints on port `5007` starting with:
```http
/api/payment/
```

## Healthchecks
Health status of the service should be available at:
```http
/api/payment/_health
```
and should return 200 OK if the service is running, otherwise 503 Service Unavailable.
