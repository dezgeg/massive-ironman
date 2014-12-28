import lejos.nxt.Button;
import lejos.nxt.ButtonListener;
import lejos.nxt.Motor;
import lejos.nxt.Sound;
import lejos.nxt.comm.BTConnection;
import lejos.nxt.comm.Bluetooth;
import lejos.nxt.comm.RConsole;
import lejos.robotics.navigation.DifferentialPilot;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.net.NXTSocketUtils;
import java.net.Socket;

public class Main {
    public static void main(String[] args) throws IOException {

        ButtonListener stop = new ButtonListener() {
            public void buttonPressed(Button b) {
                System.exit(0);
            }

            public void buttonReleased(Button b) {

            }
        };
        for (Button button : Button.BUTTONS) {
            button.addButtonListener(stop);
        }

        while (true) {
            System.out.println("Waiting for BT..");
            NXTSocketUtils.setNXTConnection(Bluetooth.waitForConnection());
            System.out.println("BT connected.");
            Socket sock = new Socket("localhost", 9001);

            DataOutputStream dataOutputStream = new DataOutputStream(sock.getOutputStream());
            DataInputStream dataInputStream = new DataInputStream(sock.getInputStream());

            DifferentialPilot diffPilot = new DifferentialPilot(56.0f, 2200.0f, Motor.B, Motor.A);
            diffPilot.setTravelSpeed(diffPilot.getMaxTravelSpeed() / 3.0f);
            //noinspection InfiniteLoopStatement
            while (true) {
                int b;
                try {
                    b = dataInputStream.readUnsignedByte();
                    System.out.println("Got byte: " + b);
                } catch (EOFException e) {
                    System.out.println("Disconnected.");
                    break;
                }
                switch (b) {
                    case ' ':
                        diffPilot.stop();
                        break;
                    case ',':
                        diffPilot.forward();
                        break;
                    case 'o':
                        diffPilot.backward();
                        break;
                    case 'a':
                        diffPilot.rotateLeft();
                        break;
                    case 'e':
                        diffPilot.rotateRight();
                        break;
                    case 'q':
                        System.exit(0);
                        break;
                    case '1':
                        diffPilot.setTravelSpeed(diffPilot.getMaxTravelSpeed() / 3.0f);
                        break;
                    case '2':
                        diffPilot.setTravelSpeed(diffPilot.getMaxTravelSpeed() / 2.0f);
                        break;
                    case '3':
                        diffPilot.setTravelSpeed(diffPilot.getMaxTravelSpeed() / 1.0f);
                        break;
                    case 'b':
                        Sound.beep();

                        break;
                }
            }
        }
    }
}
