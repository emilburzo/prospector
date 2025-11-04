# Kubernetes Deployment Guide

This guide explains how to deploy Prospector to a Kubernetes cluster (including k3s).

## Prerequisites

- Kubernetes cluster (k3s, EKS, GKE, etc.)
- kubectl configured to access your cluster
- PostgreSQL database (can be in-cluster or external)
- OpenRouter API key

## Quick Deploy

### 1. Create Namespace

```bash
kubectl create namespace prospector
```

### 2. Create Secrets

```bash
# Create secret for sensitive data
kubectl create secret generic prospector-secrets \
  --from-literal=database-url='postgresql://user:password@postgres-host:5432/prospector' \
  --from-literal=openrouter-api-key='your-api-key-here' \
  -n prospector
```

### 3. Deploy PostgreSQL (Optional)

If you don't have an external PostgreSQL database:

```yaml
# postgres.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: prospector
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: prospector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: prospector
        - name: POSTGRES_PASSWORD
          value: prospector
        - name: POSTGRES_DB
          value: prospector
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: prospector
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

Deploy it:
```bash
kubectl apply -f postgres.yaml
```

### 4. Deploy Prospector

```yaml
# prospector.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prospector
  namespace: prospector
spec:
  replicas: 2
  selector:
    matchLabels:
      app: prospector
  template:
    metadata:
      labels:
        app: prospector
    spec:
      containers:
      - name: prospector
        image: your-registry/prospector:latest  # Build and push your image first
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: prospector-secrets
              key: database-url
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: prospector-secrets
              key: openrouter-api-key
        - name: OPENROUTER_MODEL
          value: "anthropic/claude-3-haiku"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: prospector
  namespace: prospector
spec:
  selector:
    app: prospector
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: LoadBalancer  # Use NodePort for k3s if LoadBalancer is not available
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prospector
  namespace: prospector
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod  # Optional: for HTTPS
spec:
  rules:
  - host: prospector.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prospector
            port:
              number: 80
  tls:  # Optional: for HTTPS
  - hosts:
    - prospector.yourdomain.com
    secretName: prospector-tls
```

Deploy it:
```bash
kubectl apply -f prospector.yaml
```

## Building and Pushing Docker Image

Before deploying, you need to build and push the Docker image:

```bash
# Build the image
docker build -t your-registry/prospector:latest .

# Push to your registry
docker push your-registry/prospector:latest
```

For private registries, create an image pull secret:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=your-registry \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n prospector
```

Then add to your deployment:
```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
```

## k3s Specific Configuration

For k3s deployments:

1. Use NodePort instead of LoadBalancer:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: prospector
  namespace: prospector
spec:
  selector:
    app: prospector
  ports:
  - port: 80
    targetPort: 8000
    nodePort: 30080
  type: NodePort
```

2. Access via: `http://<node-ip>:30080`

3. For Traefik ingress (k3s default):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prospector
  namespace: prospector
  annotations:
    kubernetes.io/ingress.class: traefik
spec:
  rules:
  - host: prospector.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prospector
            port:
              number: 80
```

## Database Migrations

Run migrations as a Kubernetes Job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: prospector-migrate
  namespace: prospector
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: your-registry/prospector:latest
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: prospector-secrets
              key: database-url
      restartPolicy: OnFailure
```

## Monitoring and Scaling

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: prospector-hpa
  namespace: prospector
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: prospector
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Health Checks

The application provides a `/health` endpoint for liveness and readiness probes.

## Backup Strategy

For PostgreSQL backups:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: prospector
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - sh
            - -c
            - pg_dump $DATABASE_URL > /backup/prospector-$(date +%Y%m%d).sql
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: prospector-secrets
                  key: database-url
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
```

## Security Best Practices

1. **Use Network Policies** to restrict traffic
2. **Enable RBAC** with minimal permissions
3. **Use Pod Security Policies**
4. **Store secrets in a secure vault** (e.g., HashiCorp Vault, AWS Secrets Manager)
5. **Enable TLS/HTTPS** for all traffic
6. **Regularly update images** for security patches

## Troubleshooting

### Check Deployment Status
```bash
kubectl get pods -n prospector
kubectl logs -n prospector deployment/prospector
```

### Check Service
```bash
kubectl get svc -n prospector
kubectl describe svc prospector -n prospector
```

### Debug Pod Issues
```bash
kubectl describe pod <pod-name> -n prospector
kubectl exec -it <pod-name> -n prospector -- /bin/sh
```

### Database Connection Issues
```bash
# Test database connection from a pod
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -n prospector -- \
  psql $DATABASE_URL -c "SELECT version();"
```

## Production Checklist

- [ ] Database backups configured
- [ ] Secrets properly secured
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Monitoring and logging set up
- [ ] HTTPS/TLS enabled
- [ ] Horizontal autoscaling configured
- [ ] Network policies applied
- [ ] Regular security updates scheduled
- [ ] Disaster recovery plan documented
