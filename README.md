# TMH Zigbee2MQTT Multi-Instance

Este repositório publica várias Apps Zigbee2MQTT independentes para o Home
Assistant OS. Ele começa com 15 slots, de `tmh_zigbee2mqtt_01` a
`tmh_zigbee2mqtt_15`.

Cada slot usa a imagem oficial `ghcr.io/zigbee2mqtt/zigbee2mqtt-{arch}` e tem
seu próprio diretório persistente. Este projeto não recompila nem modifica o
Zigbee2MQTT.

> Regra permanente: nunca renomeie, remova ou reutilize um slug já publicado.
> Para crescer, aumente somente o número em `slots.yaml`.

## 1. Criar o repositório no GitHub

1. Entre em https://github.com e clique em **New repository**.
2. Em **Repository name**, use `tmh-zigbee2mqtt-multi`.
3. Escolha **Public**. O HAOS precisa baixar os metadados sem autenticação.
4. Não marque README, `.gitignore` ou licença; eles já estão neste pacote.
5. Clique em **Create repository**.
6. Baixe e descompacte este pacote no computador.
7. Confirme que `repository.yaml` aponta para
   `https://github.com/themodernhousebr/tmh-zigbee2mqtt-multi`.
8. Na página vazia do repositório, clique em **uploading an existing file**.
9. Arraste todo o conteúdo desta pasta, inclusive `.github`. Se seu sistema
   ocultar pastas que começam com ponto, ative a exibição de arquivos ocultos.
10. Escreva `Criar repositório multi-instância` e clique em **Commit changes**.

Confira se a raiz no GitHub mostra `repository.yaml`, `slots.yaml`, `scripts`,
`.github` e os quinze diretórios `tmh_zigbee2mqtt_XX`. Não envie uma pasta
externa contendo esses arquivos; eles precisam ficar diretamente na raiz.

## 2. Ativar as automações

1. No GitHub, abra **Settings → Actions → General**.
2. Em **Workflow permissions**, selecione **Read and write permissions**.
3. Clique em **Save**.
4. Abra a aba **Actions** e confirme a execução verde de
   **Validar repositório**.

Há três automações:

- `Gerar novos slots`: cria e salva novos diretórios quando `slots.yaml` sobe.
- `Sincronizar Zigbee2MQTT oficial`: verifica a cada seis horas a App estável oficial
  e publica a nova versão diretamente no branch `main` se houver mudança.
- `Validar repositório`: impede slugs duplicados, lacunas e dados compartilhados.

A atualização oficial é publicada automaticamente. Depois da sincronização, os
HAOS verão a nova versão quando atualizarem os metadados da loja. Antes de
atualizar uma App de produção, mantenha backups e faça o piloto em um slot de
laboratório.

## 3. Adicionar o repositório no HAOS

1. No Home Assistant, faça um backup completo em **Configurações → Sistema →
   Backups** e baixe uma cópia.
2. Abra **Configurações → Apps → Loja de Apps**.
3. Abra o menu de três pontos → **Repositórios**.
4. Cole `https://github.com/themodernhousebr/tmh-zigbee2mqtt-multi`.
5. Clique em **Adicionar** e feche a janela.
6. Procure por `TMH Zigbee2MQTT`. Devem aparecer quinze Apps numeradas.

## 4. Teste limpo antes de migrar

Use um coordenador que não pertença a uma rede em produção.

1. Instale `TMH Zigbee2MQTT 15` como slot de laboratório.
2. Não inicie ainda se o coordenador estiver sendo usado por outro software.
3. Em **Configuração**, preencha `serial.port` com o caminho estável
   `/dev/serial/by-id/...` e `serial.adapter` com o driver correto.
4. Confirme que `data_path` é `/addon_config`.
5. Se não usar o broker Mosquitto descoberto automaticamente, preencha `mqtt`.
6. Inicie a App, abra os logs e depois **Abrir interface web**.
7. Pare e inicie novamente. Confirme que a configuração e os dispositivos de
   teste continuam presentes.
8. Desinstale apenas esse slot de laboratório se desejar.

Nunca deixe duas Apps acessarem simultaneamente o mesmo coordenador. USB e
coordenadores de rede aceitam apenas uma instância Zigbee2MQTT por vez.

## 5. Inventário antes da migração

Migre uma rede por vez. Para cada App antiga, anote:

- versão exata mostrada na tela da App;
- App/repositório antigo e slot TMH de destino;
- caminho do coordenador e `serial.adapter`;
- `mqtt.server` e `mqtt.base_topic`;
- caminho atual de `data_path`;
- `pan_id`, `ext_pan_id`, `network_key` e canal (não os publique no GitHub);
- automações ou sistemas externos que usam tópicos MQTT.

Faça um backup completo imediatamente antes de cada rede. A primeira migração
deve ser um piloto e deve usar a mesma versão Zigbee2MQTT da origem. Se o
repositório TMH já estiver mais novo, veja **Fixar uma versão para a migração**.

## 6. Migrar sem reparear

Os pareamentos são preservados quando permanecem juntos: o mesmo coordenador e
todo o diretório de dados da instância, incluindo `configuration.yaml`,
`database.db`, `coordinator_backup.json`, `state.json`, conversores externos e
arquivos relacionados. Copie; não mova nem crie uma configuração nova.

O método mais claro usa uma App de arquivos/terminal que tenha acesso a
`/addon_configs` (por exemplo, Studio Code Server, Samba ou SSH devidamente
configurado). O nome da pasta contém um identificador do repositório e o slug.

1. Instale o slot TMH de destino, mas mantenha-o parado.
2. Inicie-o uma única vez com um coordenador inexistente apenas se precisar que
   o HAOS crie a pasta; em seguida, pare-o.
3. Pare a App antiga e desative **Iniciar na inicialização** e **Watchdog**.
4. Confirme novamente que a App antiga está parada.
5. Localize a pasta antiga em `/addon_configs`. Não adivinhe pelo hash: confira
   o sufixo do slug e a data/conteúdo.
6. Localize a nova pasta, terminada em `tmh_zigbee2mqtt_01` (ou o slot escolhido).
7. Copie todo o conteúdo do diretório de dados antigo para a raiz da nova pasta.
   Como o novo `data_path` é `/addon_config`, `configuration.yaml` deve terminar
   diretamente nessa raiz, não em uma subpasta adicional.
8. Na configuração da nova App, mantenha `data_path: /addon_config` e copie as
   mesmas opções `serial` e `mqtt` da App antiga.
9. Garanta que `mqtt.base_topic`, canal, `pan_id`, `ext_pan_id` e `network_key`
   permanecem idênticos.
10. Inicie somente a nova App. Verifique logs, quantidade de dispositivos,
    grupos, disponibilidade, comandos e Home Assistant MQTT Discovery.
11. Observe por pelo menos um ciclo operacional adequado ao projeto antes de
    repetir com a próxima rede.
12. Não desinstale nem apague os dados antigos até terminar o período de
    rollback definido pela equipe.

Se a instalação antiga usa `data_path: /config/alguma_pasta`, a origem fica no
diretório principal de configuração do Home Assistant. Copie o conteúdo dessa
pasta para a nova pasta de `/addon_configs`; o destino continua sendo a raiz do
novo slot.

## 7. Rollback da migração

1. Pare a nova App TMH.
2. Confirme nos logs que ela encerrou.
3. Mantenha o mesmo coordenador conectado e nunca inicie as duas Apps juntas.
4. Inicie a App antiga, que ainda aponta para sua cópia original dos dados.
5. Teste dispositivos e MQTT.

Se a nova App gravou alterações importantes depois da cópia inicial, restaure o
backup pré-migração para obter um retorno totalmente consistente. Não copie
arquivos de volta com uma das Apps em execução.

## 8. Fixar uma versão para a migração

Para separar o risco de migração do risco de upgrade:

1. Descubra a tag da App oficial que corresponde à versão antiga, por exemplo
   `v2.14.0-1`; confirme que ela realmente existe em **Tags** no repositório
   oficial.
2. Em `upstream.yaml`, troque temporariamente `ref: master` por
   `ref: vVERSAO-DA-APP`. A automação regenerará todos os slots nessa versão.
3. Valide em laboratório e migre. Não invente uma versão: a tag e a respectiva
   imagem precisam existir no repositório oficial.
4. Depois de validar a migração, volte `upstream.yaml` para `ref: master`. A
   sincronização seguinte publicará automaticamente a versão estável atual.

## 9. Aumentar de 15 para N slots

1. Abra `slots.yaml` no GitHub e clique no lápis.
2. Troque somente `slots: 15` por, por exemplo, `slots: 20`.
3. Clique em **Commit changes**.
4. Em **Actions**, aguarde `Gerar novos slots` ficar verde.
5. Atualize a loja no HAOS. Os slots 16 a 20 aparecerão.

O script recusa diminuir o valor abaixo do maior diretório existente. Essa trava
protege instalações já publicadas. Para passar de 99, primeiro adapte a regra de
numeração deliberadamente; não reutilize números antigos.

## 10. Rollback de uma atualização futura

Antes de atualizar uma App em produção, faça backup. Se uma versão oficial nova
causar problema:

1. Pare a App afetada.
2. Use o recurso de restauração/rollback oferecido pelo Home Assistant para a
   App e seus dados, ou restaure o backup criado antes do upgrade.
3. Reabra no GitHub o commit anterior do repositório TMH se quiser retirar a
   oferta da versão nova para todos os clientes.
4. Valide no piloto antes de liberar outra sincronização.

Reverter apenas o `config.json` no GitHub muda a versão oferecida, mas não
desfaz migrações internas já feitas nos dados. O backup é a proteção real.

## Segurança e manutenção

- Não coloque senhas MQTT, `network_key`, backups ou arquivos de clientes no
  GitHub.
- Mantenha o repositório público apenas com metadados e automações.
- Cada cliente adiciona o mesmo URL, mas seus dados permanecem exclusivamente
  no respectivo HAOS.
- A sincronização acompanha a App estável oficial, não a variante Edge.
- Os slots atuais suportam somente `aarch64` e `amd64`, exatamente como a imagem
  oficial corrente.

## Origem e licenças

Metadados, documentação e imagens dos slots são sincronizados de
`zigbee2mqtt/hassio-zigbee2mqtt`, licenciado sob Apache-2.0. A automação deste
repositório é MIT. Veja `THIRD_PARTY_LICENSES/zigbee2mqtt-hassio-LICENSE`.
