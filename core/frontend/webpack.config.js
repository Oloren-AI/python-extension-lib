const HtmlWebpackPlugin = require("html-webpack-plugin");
const { ModuleFederationPlugin } = require("webpack").container;

const path = require("path");
const pkg = require("./package.json");
const config = require("./config.json");

module.exports = {
  entry: "./src/index",
  mode: "development",
  stats: "errors-only",
  devServer: {
    static: {
      directory: path.join(__dirname, "dist"),
    },
    port: 3002,
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
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
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
      exposes: config["nodes"],
      shared: [
        {
          react: {
            singleton: true,
            requiredVersion: pkg.dependencies.react,
          },
        },
        {
          "react-dom": {
            singleton: true,
            requiredVersion: pkg.dependencies["react-dom"],
          },
        },
      ],
    }),
    new HtmlWebpackPlugin({
      template: "./public/index.html",
    }),
  ],
};
