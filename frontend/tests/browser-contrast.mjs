/** Contraste sRGB do texto, incluindo os fundos transparentes dos ancestrais. */
export function contrasteTexto(avaliar, seletor) {
  return avaliar(`(() => {
    const elemento = document.querySelector(${JSON.stringify(seletor)});
    if (!elemento) throw new Error('Elemento ausente na verificação de contraste');
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const contexto = canvas.getContext('2d', {willReadFrequently: true});
    contexto.fillStyle = 'white';
    contexto.fillRect(0, 0, 1, 1);
    const ancestrais = [];
    for (let atual = elemento; atual; atual = atual.parentElement) ancestrais.unshift(atual);
    for (const atual of ancestrais) {
      contexto.fillStyle = getComputedStyle(atual).backgroundColor;
      contexto.fillRect(0, 0, 1, 1);
    }
    const fundo = contexto.getImageData(0, 0, 1, 1).data;
    // O canvas converte também cores CSS oklch/oklab para sRGB.
    contexto.fillStyle = getComputedStyle(elemento).color;
    contexto.fillRect(0, 0, 1, 1);
    const texto = contexto.getImageData(0, 0, 1, 1).data;
    const luminancia = rgb => {
      const canais = Array.from(rgb).slice(0, 3).map(valor => {
        valor /= 255;
        return valor <= 0.04045 ? valor / 12.92 : ((valor + 0.055) / 1.055) ** 2.4;
      });
      return canais[0] * 0.2126 + canais[1] * 0.7152 + canais[2] * 0.0722;
    };
    const a = luminancia(texto), b = luminancia(fundo);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  })()`);
}
