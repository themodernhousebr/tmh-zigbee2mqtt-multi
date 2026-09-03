# Validação técnica

Validado em 3 de setembro de 2026 contra as fontes oficiais abaixo.

## Home Assistant

- Repositórios podem conter várias Apps; cada uma fica em pasta própria:
  https://developers.home-assistant.io/docs/apps/repository/
- `repository.yaml` é exigido na raiz:
  https://developers.home-assistant.io/docs/apps/repository/#repository-configuration
- `slug` deve ser único dentro do repositório e `version` deve corresponder à
  tag da imagem quando `image` é usada:
  https://developers.home-assistant.io/docs/apps/configuration/
- O formato JSON continua aceito para a configuração da App:
  https://developers.home-assistant.io/docs/apps/configuration/
- `addon_config` cria armazenamento próprio por App; para repositório GitHub a
  pasta hospedeira usa o hash do repositório mais o slug:
  https://developers.home-assistant.io/docs/apps/configuration/#app-configuration
- O nome interno também deriva de `{REPO}_{SLUG}`:
  https://developers.home-assistant.io/docs/apps/communication/

## Zigbee2MQTT oficial

- Repositório da App oficial:
  https://github.com/zigbee2mqtt/hassio-zigbee2mqtt
- Manifesto estável usado como fonte:
  https://github.com/zigbee2mqtt/hassio-zigbee2mqtt/blob/master/zigbee2mqtt/config.json
- Instruções oficiais de instalação, configuração e restauração:
  https://github.com/zigbee2mqtt/hassio-zigbee2mqtt#readme
- Documentação da App:
  https://github.com/zigbee2mqtt/hassio-zigbee2mqtt/blob/master/zigbee2mqtt/DOCS.md

## Resultado do desenho

- Cada slot altera somente nome, slug, descrição, URL de suporte e o padrão de
  `data_path`.
- Todos os demais campos vêm do manifesto oficial, inclusive arquiteturas,
  esquema, permissões e endereço da imagem.
- A imagem é baixada do namespace oficial; este repositório não a recompila.
- `/addon_config` é uma montagem diferente para cada slug, eliminando colisão
  entre as quinze instâncias.
- A sincronização abre Pull Request para permitir piloto e rollback antes do
  merge.

