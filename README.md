# NYC Energy Demand Forecast ML Pipeline - Airflow (Kubernetes, AKS, AZCR, Docker) - ML & API (Databricks, MLFlow, AKS) - Infastructure As Code (Terraform)

# Architecture 
# End-to-End ML Pipeline Architecture

This project implements a full **MLOps pipeline** on Azure, connecting **data ingestion, feature engineering, model training, CI/CD, and API deployment** into a reproducible workflow.

---

## 🔹 1. Data Orchestration (Airflow on AKS)
- **Airflow** runs inside **Azure Kubernetes Service (AKS)**.  
- Airflow image is built locally and pushed to **Azure Container Registry (ACR)**.  
- Airflow DAG tasks:
  1. **Ingest**: Pulls raw energy demand data from the **EIA API**.  
  2. **Bronze layer (ADLS Gen2)**: Stores raw ingested data.  
  3. **Silver layer (ADLS Gen2)**: Pre-processed & cleaned data.  
  4. **Gold layer (ADLS Gen2)**: Aggregated + feature-engineered dataset ready for modeling.  

---

## 🔹 2. Model Training & Registry (Databricks + MLflow)
- **Databricks** reads the **Gold layer** data from ADLS.  
- **MLflow** used for:
  - Training **multiple candidate models** (e.g., XGBoost, Random Forest, LSTM).  
  - Logging metrics, artifacts, and parameters.  
  - Comparing model performance and selecting the **best model**.  
- The **best model.pkl** is exported and versioned locally.  

---

## 🔹 3. CI/CD Deployment (GitHub Actions → ACR → AKS)
- When the `model.pkl` file is **committed to `main` branch**, it triggers the **GitHub Actions CI/CD pipeline**:
  1. **Build Docker image** (FastAPI + Dash app serving the model).  
  2. **Push image to ACR**.  
  3. **Deploy to AKS** via `kubectl set image` update.  
  4. **Dashboard service** is refreshed with the new model image.  

- The **Dash Web App**:
  - Calls the trained model via API.  
  - Provides **interactive forecasts** for future energy demand dates.  

---

## 📊 Architecture Diagram

```mermaid
flowchart TD
    %% Section 1: Data
    subgraph A[Data Orchestration: Airflow on AKS]
        A1[Ingest EIA API Data] --> A2[Bronze Layer ADLS Gen2]
        A2 --> A3[Silver Layer ADLS Gen2]
        A3 --> A4[Gold Layer ADLS Gen2]
    end

    %% Section 2: ML
    subgraph B[Model Training: Databricks + MLflow]
        A4 --> B1[Databricks Training Jobs]
        B1 --> B2[MLflow Tracking]
        B2 --> B3[Best Model Selected]
        B3 --> B4[Export model.pkl]
    end

    %% Section 3: CI/CD + Serving
    subgraph C[Deployment: GitHub Actions + ACR + AKS]
        B4 --> C1[Commit model.pkl to GitHub main]
        C1 --> C2[GitHub Actions Build & Push Docker Image to ACR]
        C2 --> C3[Deploy to AKS]
        C3 --> C4[Dash Web App / FastAPI Service]
        C4 --> C5[Forecast API for Future Dates]
    end
  ```
# Command Line Interfaces Used:
 - AZ CLI (Azure)
 - Terraform CLI
 - Kubernetes (kubectl)


# Key Services Used:
 - AKS (Kubernetes Cluster VM Azure)
 - Azure Container Registry (AZCR)
 - Azure Key Vault
 - Databricks
 - Terraform
 - Dash App
 - Airflow
 - Docker
 - Python

# CI/CD Pipeline (GitHub Actions → Azure)

This project uses **GitHub Actions** to automate the build and deployment process.

## Workflow Overview
- **Trigger**: On every push to the `main` branch
- **Steps**:
  1. **Build Docker image** using project `Dockerfile`
  2. **Push image** to Azure Container Registry (ACR)
  3. **Deploy to AKS** by updating Kubernetes deployment with the new image
  4. **Rollout verification** ensures pods are healthy

## Key Components
- **GitHub Actions** workflow defined in [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)  
- **Helper scripts**:
  - `scripts/build_docker.sh` → Builds the Docker image
  - `scripts/push_azcr.sh` → Tags & pushes image to ACR
  - `scripts/deploy_aks.sh` → Updates AKS deployment and waits for rollout

## Example Workflow Diagram

```mermaid
flowchart TD
    A[Developer Commit to main] --> B[GitHub Actions Runner]
    B --> C[Build Docker Image]
    C --> D[Push Image to Azure Container Registry]
    D --> E[Deploy Updated Image to AKS]
    E --> F[App Running in Kubernetes Pods]
```

# Terraform:












# Airflow









# ML Deployment to AKS

## Dash Web App Demonstration Model Application

<img width="2836" height="1278" alt="image" src="https://github.com/user-attachments/assets/ca936219-95b4-4f1e-b4b5-ee1fead29b3a" />
