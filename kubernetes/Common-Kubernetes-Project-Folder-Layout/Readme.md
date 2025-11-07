The default Kubernetes setup does not impose any strict folder structure for manifest files. Users and teams typically organize Kubernetes manifests in folders by the types of resources, environment, or project needs. For example, a common folder layout for manifests might have separate directories for deployments, services, configmaps, and network policies to keep things modular and manageable.

A common practice is to create a dedicated folder such as networkpolicies/ or include network policies alongside other related manifests, e.g., in manifests/networkpolicies/ within your project repository. There is no fixed or predefined "default" folder named specifically for network policies created by Kubernetes itself; this organization is up to the user.

Typical community/project folder structure example:

<img width="702" height="370" alt="image" src="https://github.com/user-attachments/assets/01e3a967-62f0-4b92-bfb3-61c9c5d39151" />
