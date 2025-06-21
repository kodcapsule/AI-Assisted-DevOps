# AI-Assisted DevOps: Building a Multi-Tool-AI-Agent | CI/CD Agent
![Multi-Tool AI Agent](./images/Multi-tool%20AI%20Agent.png)

This project leverages Google's Agent Development Kit (ADK) to create a multi-agent system for DevOps automation. The agents are designed to collaborate and streamline various DevOps tasks, enhancing efficiency and reducing manual intervention.

## Features

- **Multi-Agent Architecture**: Implements multiple agents working together to perform DevOps tasks.
- **AI-Powered Automation**: Uses AI to optimize workflows and decision-making.
- **Extensibility**: Easily customizable to add new agents or extend existing functionalities.
- **Integration**: Supports integration with popular DevOps tools and platforms.

## Prerequisites

- Python 3.8 or higher
- Google Agent Development Kit (ADK)
- Access to required DevOps tools (e.g., Jenkins, Kubernetes, AWS CLI)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/ai-assisted-devops.git
    cd ai-assisted-devops
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables for your DevOps tools.

## Usage

1. Configure the agents in the `config/agents.yaml` file.
2. Run the main script to start the multi-agent system:
    ```bash
    python main.py
    ```

## Contributing

Contributions are welcome! Please follow the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Google for providing the Agent Development Kit (ADK).
- Open-source contributors for their tools and libraries.
