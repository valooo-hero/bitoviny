export function jeJpeg(bajty) {
  return bajty[0] === 0xff && bajty[1] === 0xd8 && bajty[2] === 0xff;
}

export function jeWebp(bajty) {
  return bajty[0] === 0x52 && bajty[1] === 0x49 && bajty[2] === 0x46 && bajty[3] === 0x46 &&
    bajty[8] === 0x57 && bajty[9] === 0x45 && bajty[10] === 0x42 && bajty[11] === 0x50;
}
