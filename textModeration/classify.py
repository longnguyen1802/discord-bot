from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline
import os
import sys
import json
model_path = "mymodel"
tokenizer = AutoTokenizer.from_pretrained(model_path,local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path,local_files_only=True)
pipeline =  TextClassificationPipeline(model=model, tokenizer=tokenizer)
def classify(text_message):
    # disable stdout
    null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
    save = os.dup(1), os.dup(2)
    os.dup2(null_fds[0], 1)
    os.dup2(null_fds[1], 2)
    score = pipeline(text_message)
    # enable stdout
    os.dup2(save[0], 1)
    os.dup2(save[1], 2)
    os.close(null_fds[0])
    os.close(null_fds[1])
    print(json.dumps(score))

def main(argv):
    message = sys.argv[1:]
    text_message = ' '.join(message)
    #text_message = "fuck you"
    classify(text_message)


if __name__ == "__main__":
    main(sys.argv)