package main

import (
	"log"
	"net/http"

	"github.com/Azure/azure-storage-blob-go/azblob"
	"github.com/gorilla/mux"
)

// LINEアクセス用
const (
	LineChannelSecret = os.Getenv("LINE_CHANNEL_SECRET")
	LineAccessToken   = os.Getenv("LINE_CHANNEL_ACCESS_TOKEN")
)

// Azure Storage Containerの名前
const (
	ContainerName                         = os.Getenv("CONTAINER_NAME")
	AzureStorageContainerConnectionString = os.Getenv("ASC_CONNECTION_STRING")
)

// Azure Table Strageの名前，アクセスキー
const (
	StrageKey                = os.Getenv("AZURE_STRAGE_KEY")
	StrageName               = os.Getenv("AZURE_STRAGE_NAME")
	AzureTableTrackingNumber = "TrackingNumberTable"
)

func main() {
	port := os.Getenv("PORT")

	if port == "" {
		log.Fatal("$PORT must be set")
	}

	bot, err := linebot.New(
		LineChannelSecret,
		LineAccessToken,
	)

	if err != nil {
		log.Fatal(err)
	}

	// Setup HTTP Server for receiving requests from LINE platform
	http.HandleFunc("/callback", func(w http.ResponseWriter, req *http.Request) {
		events, err := bot.ParseRequest(req)
		if err != nil {
			if err == linebot.ErrInvalidSignature {
				w.WriteHeader(400)
			} else {
				w.WriteHeader(500)
			}
			return
		}
		for _, event := range events {
			if event.Type == linebot.EventTypeMessage {
				switch message := event.Message.(type) {
				case *linebot.TextMessage:
					if event.ReplyToken == "00000000000000000000000000000000" {
						return
					}
					if _, err = bot.ReplyMessage(event.ReplyToken, linebot.NewTextMessage(parse(message.Text))).Do(); err != nil {
						log.Print(err)
					}
				}
			}
		}
	})
	// This is just sample code.
	// For actual use, you must support HTTPS by using `ListenAndServeTLS`, a reverse proxy or something else.
	if err := http.ListenAndServe(":"+os.Getenv("PORT"), nil); err != nil {
		log.Fatal(err)
	}
}

func ReplyMessageText(string message) {

}
