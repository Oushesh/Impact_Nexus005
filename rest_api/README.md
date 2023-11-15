# Creating image for rest-api 

  ```bash
  docker build -t smart-evidence:rest-api -f rest_api/Dockerfile-old .
  ```
# Run service

```bash
  docker run smart-evidence:rest-api -p 8000:8000
```
