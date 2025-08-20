job "docs" {
  datacenters = ["dc1"]
  type = "service"

  group "web" {
    task "app" {
      driver = "docker"
      
      config {
        image = "ghcr.io/aisystant/docs:latest"
        ports = ["http"]
      }
      
      resources {
        cpu    = 100
        memory = 128
      }
      
      service {
        name = "docs"
        port = "http"
        
        check {
          type     = "http"
          path     = "/"
          interval = "10s"
          timeout  = "3s"
        }
      }
    }
    
    network {
      port "http" {
        static = 8080
      }
    }
  }
}
