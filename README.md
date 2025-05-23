<div align="center">

# FIAP Hackathon - Lambda Video Receive

![GitHub Release Date](https://img.shields.io/badge/Release%20Date-Abril%202025-yellowgreen)
![](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellowgreen)
<br>
![](https://img.shields.io/badge/Version-%20v1.0.0-brightgreen)
</div>

## 💻 Descrição

Este repositório é responsável criar a Lambda do recebmento da mensagem do video da aplicação.

## 🛠 Tecnologias Utilizadas

<div align="center">

![AWSLAMBDA](https://img.shields.io/badge/AWS%20Lambda-FF9900.svg?style=for-the-badge&logo=AWS-Lambda&logoColor=white)
![GithubActions](https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=for-the-badge&logo=GitHub-Actions&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)

</div>

## ⚙️ Configuração

### Desenvolvimento

- **[Terraform](https://www.terraform.io/)**: Site oficial do Terraform.
- **[AWS](https://aws.amazon.com/pt/)**: Site oficial da AWS.
- **[Python](https://docs.python.org/pt-br/3/)**: Documentação oficial do Python.

## 🚀 Execução

### Subindo a Lambda do recebmento da mensagem do video

  Caso deseje subir a Lambda do recebmento da mensagem do video, basta seguir os seguintes passos:
  
  1. Certificar que o Terraform esteja instalado executando o comando `terraform --version`;
  2. Certificar que o `aws cli` está instalado e configurado com as credenciais da sua conta AWS;
  3. Acessar a pasta `terraform` que contém os arquivos que irão criar a Lambda;
  4. Inicializar o Terraform no projeto `terraform init`;
  5. Verificar que o script do Terraform é valido rodando o comando `terraform validate`;
  6. Executar o comando `terraform plan` para executar o planejamento da execução/implementação;
  7. Executar o comando `terraform apply` para criar a Lambda;
  8. Após a execução do Terraform finalizar, verificar se a Lambda subiu corretamente na AWS;
