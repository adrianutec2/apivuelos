terraform {
  backend "gcs" {
    bucket = "bucket-tfstate-303be0fc0cfd670f"
    prefix = "terraform/state"
  }
}