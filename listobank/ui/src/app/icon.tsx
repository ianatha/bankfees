import { ImageResponse } from "next/og";

export const size = {
  width: 32,
  height: 32,
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      // ImageResponse JSX element
      <div
        style={{
          position: "relative",
          fontSize: 32,
          background: "transparent",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 32,
            height: 32,
            position: "relative",
          }}
        >
          🔎
          <span
            style={{
              position: "absolute",
              top: -2,
              right: -2,
              fontSize: 32,
              color: "#111111",
              fontWeight: "bold",
            }}
          >
            €
          </span>
        </span>
      </div>
    ),
    {
      ...size,
    }
  );
}
