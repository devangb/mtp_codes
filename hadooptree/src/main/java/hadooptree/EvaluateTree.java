package hadooptree;

import hadooptree.tree.Tree;
import hadooptree.tree.Node;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.Reader;
import java.util.ArrayList;
import org.jdom.Element;
import org.jdom.input.SAXBuilder;

public class EvaluateTree {

  public static void main(String[] args) throws Exception {

    if (args.length != 2) {
      System.out.println("Expected: java -jar HadoopTree.jar <treeXML> <testCSV>");
      return;
    }


    SAXBuilder saxBuilder = new SAXBuilder();
    Reader xmlIn = new FileReader(args[0]);

    Element treeElement = saxBuilder.build(xmlIn).getRootElement();
    Tree tree = Tree.fromElement(treeElement);

    BufferedReader reader = new BufferedReader(new FileReader(args[1]));
    long errors = 0;
    long total = 0;
    int [][] confmat = new int[10][10];
    while (reader.ready()) {
      String line = reader.readLine();
      line = line.trim();
      if (line.isEmpty()) {
        continue;
      }

      String[] tokens = line.split(",");
      ArrayList<Object> instance = new ArrayList<Object>();

      for (String token : tokens) {
        Object value;
        try {
          value = Double.valueOf(token);
        } catch (NumberFormatException e) {
          value = token;
        }
        instance.add(value);
      }

      Node node = tree.evalToNode(instance);
      String predictedClass = node.getPredictedClass();
      String actualClass = (String) instance.get(tree.getObjectiveFieldIndex());

      int pred;
      int act;
        if(predictedClass=="Nothing_in_hand") pred = 0;
        else if(predictedClass=="One_pair") pred = 1;
        else if(predictedClass=="Two_pairs") pred = 2;
        else if(predictedClass=="Three_of_a_kind") pred = 3;
        else if(predictedClass=="Straight") pred = 4;
        else if(predictedClass=="Flush") pred = 5;
        else if(predictedClass=="Full_house") pred = 6;
        else if( predictedClass=="Four_of_a_kind") pred = 7;
        else if(predictedClass=="Straight_flush") pred = 8;
        else if (predictedClass=="Royal_flush") pred = 9;
        else pred =0;

        if (actualClass == "Nothing_in_hand"){ act = 0;}
        else if (actualClass == "One_pair") {
          act = 1;
        }
        else if (actualClass == "Two_pairs"){ act = 2;}
        else if (actualClass == "Three_of_a_kind") act = 3;
        else if (actualClass == "Straight") act = 4;
        else if (actualClass == "Flush") act = 5;
        else if (actualClass == "Full_house") act = 6;
        else if (actualClass == "Four_of_a_kind") act = 7;
        else if (actualClass == "Straight_flush") act = 8;
        else if (actualClass == "Royal_flush") act = 9;
        else act =0;

      //System.out.println(predictedClass + " " + actualClass +"\n");
      confmat[pred][act]++;
      if (!predictedClass.equals(actualClass)) {
        errors++;
      }

      total++;
    }

    long correct = total - errors;
    double successRate = (double) correct / (double) total;
    successRate *= 100;
    for(int i = 0; i<10; i++)
{
    for(int j = 0; j<10; j++)
    {
        System.out.print(confmat[i][j]);
    }
    System.out.println();
}
    System.out.println("Result: " + correct + "/" + total + " --- " + successRate);

  }
}
