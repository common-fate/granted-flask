# granted-flask

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)


# ecs-flask-recording-demo

Demo Flask Shell provider for Granted

## How to use

Check out the `demo-providers-recording` branch of Granted Approvals. You'll want to configure your providers as per the below YAML.

```yml
version: 2
deployment:
  stackName: granted-approvals-chris10
  account: "385788203919"
  region: us-east-1
  release: ""
  dev: true
  parameters:
    CognitoDomainPrefix: ""
    AdministratorGroupID: granted_administrators
    ProviderConfiguration:
      testvault:
        uses: commonfate/testvault@v1
        with:
          apiUrl: https://prod.testvault.granted.run
          uniqueId: 2DOhMnswyn47DXuRKG8EbkTSPHp
      flask-shell:
        uses: commonfate/demo@v1
        with:
          instructions: Copy the Access Token below and then run 'flask shell' to access the audited Flask shell.
          options:
            server:
              - label: ECS Demo
                value: ecs-demo
          schema:
            properties:
              server:
                title: Server
                type: string
            required:
              - server
            type: object
          type: python
```

You'll need to update the URL in `GrantedConsole` to point to the REST API URL in your dev deployment of Granted. The URL should look similar to

```
https://a9yi770x54.execute-api.us-east-1.amazonaws.com/prod/webhook/v1/events-recorder
```

To get the Python shell up and running:

```bash
poetry install
poetry shell
pip install -e ./granted_flask/ # this installs the granted_flask package which overrides the 'flask shell' command
flask shell
```

If this doesn't work, `poetry run python shell.py` should also work.

## How it works

It uses a custom class which overrides `code.InteractiveConsole` to send the commands to Granted before they are run.
