FROM public.ecr.aws/lambda/python:3.13

# Install dependencies for OpenSCAD
RUN dnf install -y harfbuzz libXrender libXext libSM libICE libX11 libglvnd-glx mesa-libGL mesa-libEGL libglvnd-opengl

# Try older AppImage from 2021 (should be compatible with GLIBC 2.34)
RUN curl -L https://files.openscad.org/OpenSCAD-2021.01-x86_64.AppImage -o /openscad.AppImage && \
    chmod +x /openscad.AppImage && \
    /openscad.AppImage --appimage-extract && \
    mv squashfs-root /openscad && \
    rm /openscad.AppImage && \
    ln -s /openscad/usr/bin/openscad /usr/local/bin/openscad

# Copy function code
COPY src/app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]