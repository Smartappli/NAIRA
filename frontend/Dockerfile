FROM node:18-alpine

# Installer pnpm
RUN npm install -g pnpm

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY package.json pnpm-lock.yaml ./

# Installer les dépendances
RUN pnpm install

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 3000

# Commande par défaut
CMD ["pnpm", "dev", "--host", "0.0.0.0"] 