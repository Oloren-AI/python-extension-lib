const HtmlWebpackPlugin = require("html-webpack-plugin");
const ModuleFederationPlugin = require("webpack/lib/container/ModuleFederationPlugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const webpack = require("webpack");

const config = require("./oloren.json");
const OlorenCore = require("@oloren/core");
const path = require("path");
const deps = require("./package.json").dependencies;

const fs = require("fs");
if (!fs.existsSync("./static")) {
  fs.mkdirSync("./static");
}
fs.writeFileSync(
  "./static/directory",
  JSON.stringify(OlorenCore.configToDirectory(config), null, 2),
  "utf-8"
);

module.exports = {
  entry: "./src/index",
  mode: "development",
  stats: "errors-only",
  devServer: {
    static: {
      directory: path.join(__dirname, "dist"),
    },
    port: 8080,
  },
  output: {
    publicPath: "auto",
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.tsx?$/,
        loader: "babel-loader",
        exclude: /node_modules/,
        options: {
          presets: ["@babel/preset-react", "@babel/preset-typescript"],
        },
      },
    ],
  },
  plugins: [
    new ModuleFederationPlugin({
      name: config["name"],
      filename: "remoteEntry.js",
      remotes: {},
      exposes: OlorenCore.configToWebpack(config),
      shared: [
        {
          react: {
            singleton: true,
            requiredVersion: deps.react,
          },
        },
        {
          "react-dom": {
            singleton: true,
            requiredVersion: deps["react-dom"],
          },
        },
      ],
    }),
    new CopyWebpackPlugin({
      patterns: [{ from: "static" }],
    }),
    new HtmlWebpackPlugin({
      template: "./public/index.html",
    }),
    new webpack.ProvidePlugin({
      process: "process/browser",
    }),
  ],
};
