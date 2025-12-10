# Documentação do Módulo: syscheckup.py

## 🛠 Nome do Módulo

`syscheckup.py`

## 📂 Localização

`shadowsec-toolkit/modules/syscheckup.py`

## 🧠 Função

Esse módulo realiza uma verificação completa e automatizada no sistema operacional, cobrindo tarefas de manutenção e segurança essenciais. É o primeiro módulo do ShadowSec Toolkit e pode ser usado periodicamente por administradores de sistema ou usuários preocupados com a saúde e segurança da máquina.

---

## ⚙️ Funcionalidades

O script realiza as seguintes operações:

1. **Verificação e aplicação de atualizações do sistema**
   Atualiza os pacotes da distribuição Linux (compatível com sistemas baseados em `apt`, como Debian e Ubuntu).

2. **Limpeza de pacotes órfãos**
   Usa `deborphan` para encontrar e sugerir remoção de bibliotecas não utilizadas.

3. **Verificação de antivírus**
   Executa uma varredura rápida com o ClamAV, se instalado.

4. **Verificação e status do firewall UFW**
   Garante que o firewall esteja ativo e exibe o status atual.

5. **Listagem de backups**
   Procura por diretórios nomeados `backup` no sistema e os lista para o usuário.

---

## 🧪 Requisitos

* Sistema Linux com `apt` (Debian, Ubuntu)
* Permissão de superusuário (root ou via sudo)
* Programas necessários:

  * `clamav`
  * `ufw`
  * `deborphan`

Esses pacotes são checados e instalados automaticamente, se não estiverem presentes.

---

## ▶️ Como Executar

```bash
chmod +x modules/system_checkup.sh
sudo ./modules/system_checkup.sh
```

---

## 📝 Notas

* O script avisa ao final que os módulos estão prontos para serem utilizados.
* O usuário precisa inserir a senha de `sudo` para execução correta.

---

## 🔒 Observação de Segurança

Este script executa comandos privilegiados. Por isso, é recomendável verificar o código antes da execução, especialmente em ambientes de produção.

---

## 📌 Próximos Passos

* Criar opções de log detalhado (`--log`)
* Adicionar parâmetros CLI para executar partes específicas da verificação
* Suporte para distribuições com `dnf` e `pacman`

---

Autor: Luciano Valadão
Data: 2025

