import { EnvStore } from "vault-file";

console.log(
  `Loading Vault File integration... ${process.env.VAULT_SECRET_FILE}`
);

// EnvStore.onStartup reads from VAULT_SECRET_FILE env var by default if no arg passed
// or we can pass it explicitly.
// Since this module acts as an env loader, it's executed before lifecycle hooks.

await EnvStore.onStartup(process.env.VAULT_SECRET_FILE || ".env");
console.log(`Vault File loaded`);
