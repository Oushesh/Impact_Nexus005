FROM python:3.10

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y awscli && \
    apt-get install -y curl git && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install git-lfs
RUN git lfs install    

# set working directory
RUN mkdir /code
WORKDIR /code

# Download ML Models
RUN git clone  https://huggingface.co/cross-encoder/nli-deberta-v3-xsmall models/nli-deberta-v3-xsmall/
RUN git clone  https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 models/all-MiniLM-L6-v2/
RUN rm /code/models/all-MiniLM-L6-v2/rust_model.ot /code/models/all-MiniLM-L6-v2/tf_model.h5 

# Copy requirements
COPY rest_api/requirements.txt /code/

RUN apt-get install libgeos-dev -y

# Install Dependencies
RUN bash -c "pip install --upgrade pip"

ENV TRANSFORMERS_OFFLINE=1
ENV PYTHONPATH=/code

# Installing dependencies with pip for now
RUN pip install torch==1.12.1+cpu torchvision==0.13.1+cpu torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cpu
RUN bash -c "pip install -r requirements.txt"

# TODO: cp only necessary directories
COPY . /code/



ENTRYPOINT [ "python","rest_api/application.py" ]
