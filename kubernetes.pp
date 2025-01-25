class { 'kubernetes':
  kubeconfig => '/path/to/kubeconfig',  # Asegúrate de que el archivo kubeconfig esté accesible
}

kubernetes::resource::deployment { 'finconecta-bot':
  ensure   => 'present',
  replicas => 3,
  image    => 'codelogman/finconecta_bot:latest',  # Tu imagen de Docker
  port     => 8080,
  service  => true,
}

kubernetes::resource::service { 'finconecta-bot-service':
  ensure     => 'present',
  app_name   => 'finconecta-bot',
  port       => 8080,
  targetPort => 8080,
  type       => 'LoadBalancer',
}

