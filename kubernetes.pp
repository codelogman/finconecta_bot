class { 'kubernetes':
  kubeconfig => '/path/to/kubeconfig',  
}

kubernetes::resource::deployment { 'finconecta_bot':
  ensure   => 'present',
  replicas => 3,
  image    => 'codelogman/finconecta_bot:latest',  
  port     => 8080,
  service  => true,
}

kubernetes::resource::service { 'finconecta-bot-service':
  ensure     => 'present',
  app_name   => 'finconecta_bot',
  port       => 8080,
  targetPort => 8080,
  type       => 'LoadBalancer',
}

