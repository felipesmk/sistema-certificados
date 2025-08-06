#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO DE REDE E FIREWALL"
echo "========================================"
echo

# Obter IP da VM
echo "[1/4] Obtendo IP da VM..."
hostname -I
echo

# Verificar porta 5000
echo "[2/4] Verificando porta 5000..."
if lsof -i :5000 > /dev/null 2>&1; then
    echo "AVISO: Porta 5000 ja esta em uso!"
    lsof -i :5000
    echo
fi

# Configurar firewall
echo "[3/4] Configurando firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 5000
    echo "Firewall UFW configurado com sucesso!"
elif command -v iptables &> /dev/null; then
    sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
    echo "Firewall iptables configurado com sucesso!"
else
    echo "AVISO: Nenhum firewall detectado!"
fi

# Testar conectividade
echo "[4/4] Testando conectividade..."
echo "Testando localhost..."
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "Localhost: OK"
else
    echo "Localhost: FALHOU (aplicacao nao esta rodando)"
fi

echo
echo "========================================"
echo "    CONFIGURACAO DE REDE CONCLUIDA"
echo "========================================"
echo
echo "Para acessar de outras maquinas:"
echo "http://[IP-DA-VM]:5000"
echo
echo "Para verificar IP novamente: hostname -I"
echo "Para testar conectividade: curl http://localhost:5000"
echo 