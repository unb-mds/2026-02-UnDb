import { ConfirmationClient } from "./confirmation-client";

export default async function ConfirmarEmailPage({
  searchParams,
}: PageProps<"/confirmar-email">) {
  const parametros = await searchParams;
  const token = typeof parametros.token === "string" ? parametros.token : undefined;
  return <ConfirmationClient token={token} />;
}
