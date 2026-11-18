export function jeJpeg(bajty) {
  return bajty[0] === 0xff && bajty[1] === 0xd8 && bajty[2] === 0xff;
}
